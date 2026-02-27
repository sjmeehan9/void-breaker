"""Pooled sprite particle effects for combat and shop feedback."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path

import arcade
from asterax.app.src.config.game_config import AsteroidSize


@dataclass(slots=True)
class _PooledParticle:
    """Reusable particle state bound to a pre-allocated sprite."""

    sprite: arcade.Sprite
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    lifetime: float = 0.0
    max_lifetime: float = 1.0
    active: bool = False
    activated_at: int = 0


class ParticleSystem:
    """Manage pooled short-lived particles with a hard active cap."""

    def __init__(
        self,
        particles: arcade.SpriteList[arcade.Sprite] | None = None,
        rng: random.Random | None = None,
        max_particles: int = 300,
    ) -> None:
        """Initialise pooled particle storage and randomness source."""
        self._particles = particles if particles is not None else arcade.SpriteList()
        self._rng = rng if rng is not None else random.Random()
        self._max_particles = max(1, max_particles)
        self._activation_tick = 0
        particle_texture_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "sprites"
            / "particle_dot.png"
        )
        self._pool: list[_PooledParticle] = []
        self._pooled_sprite_ids: set[int] = set()
        for _ in range(self._max_particles):
            sprite = arcade.Sprite(
                str(particle_texture_path), center_x=-1000.0, center_y=-1000.0
            )
            sprite.alpha = 0
            self._particles.append(sprite)
            self._pool.append(_PooledParticle(sprite=sprite))
            self._pooled_sprite_ids.add(id(sprite))

    @property
    def particles(self) -> arcade.SpriteList[arcade.Sprite]:
        """Expose active particle list."""
        return self._particles

    @property
    def max_particles(self) -> int:
        """Return total number of pooled particle slots."""
        return self._max_particles

    @property
    def active_particle_count(self) -> int:
        """Return currently active particles."""
        return sum(1 for particle in self._pool if particle.active)

    def spawn_explosion(
        self, position: tuple[float, float], size: AsteroidSize
    ) -> None:
        """Backward-compatible asteroid explosion entrypoint."""
        if size is AsteroidSize.LARGE:
            self.emit_explosion(position[0], position[1], "large")
            return
        if size is AsteroidSize.MEDIUM:
            self.emit_explosion(position[0], position[1], "medium")
            return
        self.emit_explosion(position[0], position[1], "small")

    def emit_explosion(
        self,
        x: float,
        y: float,
        size: str,
        color: tuple[int, int, int] = (255, 180, 70),
    ) -> None:
        """Emit a radial explosion burst with size-scaled profile."""
        profile = _explosion_profile(size)
        self._emit_radial(
            x=x,
            y=y,
            count=profile[0],
            speed_range=profile[1],
            lifetime_range=profile[2],
            color=color,
            scale_range=profile[3],
        )

    def emit_thrust(self, x: float, y: float, angle: float) -> None:
        """Emit one thrust-trail particle opposite ship heading."""
        radians = math.radians(angle + 90.0)
        base_velocity_x = -math.cos(radians)
        base_velocity_y = -math.sin(radians)
        speed = self._rng.uniform(30.0, 80.0)
        spread = self._rng.uniform(-0.35, 0.35)
        cosine = math.cos(spread)
        sine = math.sin(spread)
        vx = (base_velocity_x * cosine - base_velocity_y * sine) * speed
        vy = (base_velocity_x * sine + base_velocity_y * cosine) * speed
        self._activate_particle(
            x=x,
            y=y,
            velocity_x=vx,
            velocity_y=vy,
            lifetime=self._rng.uniform(0.2, 0.4),
            color=(190, 225, 255),
            scale=self._rng.uniform(0.22, 0.38),
        )

    def emit_sparkle(self, x: float, y: float) -> None:
        """Emit pickup sparkle particles."""
        self._emit_radial(
            x=x,
            y=y,
            count=6,
            speed_range=(20.0, 60.0),
            lifetime_range=(0.3, 0.5),
            color=(255, 220, 90),
            scale_range=(0.2, 0.35),
        )

    def emit_damage_flash(self, x: float, y: float) -> None:
        """Emit a compact impact burst on damage contact."""
        self._emit_radial(
            x=x,
            y=y,
            count=4,
            speed_range=(40.0, 100.0),
            lifetime_range=(0.15, 0.3),
            color=(255, 90, 90),
            scale_range=(0.25, 0.4),
        )

    def emit_purchase_burst(
        self,
        x: float,
        y: float,
        color: tuple[int, int, int] = (140, 255, 200),
    ) -> None:
        """Emit confirmation burst for successful shop interactions."""
        self._emit_radial(
            x=x,
            y=y,
            count=10,
            speed_range=(30.0, 80.0),
            lifetime_range=(0.3, 0.6),
            color=color,
            scale_range=(0.22, 0.4),
        )

    def update(self, dt: float) -> None:
        """Advance active particles and recycle expired instances."""
        for particle in self._pool:
            if not particle.active:
                continue
            particle.sprite.center_x += particle.velocity_x * dt
            particle.sprite.center_y += particle.velocity_y * dt
            particle.lifetime -= dt
            if particle.lifetime <= 0.0:
                self._deactivate_particle(particle)
                continue
            alpha_ratio = max(0.0, min(1.0, particle.lifetime / particle.max_lifetime))
            particle.sprite.alpha = int(255 * alpha_ratio)

        for sprite in list(self._particles):
            if id(sprite) in self._pooled_sprite_ids:
                continue
            update_particle = getattr(sprite, "update_particle", None)
            if callable(update_particle):
                update_particle(dt)
                continue
            sprite.update()

    def draw(self) -> None:
        """Draw all active particles."""
        self._particles.draw()

    def _emit_radial(
        self,
        x: float,
        y: float,
        count: int,
        speed_range: tuple[float, float],
        lifetime_range: tuple[float, float],
        color: tuple[int, int, int],
        scale_range: tuple[float, float],
    ) -> None:
        """Emit a radial burst using pooled particle slots."""
        for _ in range(max(0, count)):
            angle = self._rng.uniform(0.0, math.tau)
            speed = self._rng.uniform(*speed_range)
            self._activate_particle(
                x=x,
                y=y,
                velocity_x=math.cos(angle) * speed,
                velocity_y=math.sin(angle) * speed,
                lifetime=self._rng.uniform(*lifetime_range),
                color=color,
                scale=self._rng.uniform(*scale_range),
            )

    def _activate_particle(
        self,
        x: float,
        y: float,
        velocity_x: float,
        velocity_y: float,
        lifetime: float,
        color: tuple[int, int, int],
        scale: float,
    ) -> None:
        """Reserve a pool slot and activate one particle."""
        particle = self._next_available_particle()
        self._activation_tick += 1
        particle.sprite.center_x = x
        particle.sprite.center_y = y
        particle.sprite.color = color
        particle.sprite.scale = scale
        particle.sprite.alpha = 255
        particle.velocity_x = velocity_x
        particle.velocity_y = velocity_y
        particle.lifetime = max(0.01, lifetime)
        particle.max_lifetime = particle.lifetime
        particle.active = True
        particle.activated_at = self._activation_tick

    def _next_available_particle(self) -> _PooledParticle:
        """Return an inactive particle, or recycle the oldest active slot."""
        for particle in self._pool:
            if not particle.active:
                return particle
        oldest = min(self._pool, key=lambda particle: particle.activated_at)
        self._deactivate_particle(oldest)
        return oldest

    @staticmethod
    def _deactivate_particle(particle: _PooledParticle) -> None:
        """Reset a particle slot back to inactive state."""
        particle.active = False
        particle.lifetime = 0.0
        particle.max_lifetime = 1.0
        particle.velocity_x = 0.0
        particle.velocity_y = 0.0
        particle.sprite.alpha = 0
        particle.sprite.center_x = -1000.0
        particle.sprite.center_y = -1000.0


def _explosion_profile(
    size: str,
) -> tuple[int, tuple[float, float], tuple[float, float], tuple[float, float]]:
    """Map explosion size label to count, speed, lifetime, and scale ranges."""
    normalized_size = size.lower().strip()
    if normalized_size == "large":
        return (25, (100.0, 250.0), (0.5, 1.0), (0.25, 0.5))
    if normalized_size == "medium":
        return (15, (80.0, 200.0), (0.4, 0.8), (0.22, 0.45))
    return (8, (50.0, 150.0), (0.3, 0.6), (0.2, 0.4))
