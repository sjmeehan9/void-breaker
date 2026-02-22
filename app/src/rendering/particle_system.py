"""Simple sprite-based explosion particle effects."""

from __future__ import annotations

import math
import random
from pathlib import Path

import arcade
from asterax.app.src.config.game_config import AsteroidSize


class _ExplosionParticle(arcade.Sprite):
    """Internal particle sprite with velocity and lifetime bookkeeping."""

    def __init__(
        self,
        texture_path: Path,
        center_x: float,
        center_y: float,
        velocity_x: float,
        velocity_y: float,
        lifetime: float,
    ) -> None:
        """Create a particle with motion and finite lifetime."""
        super().__init__(str(texture_path), center_x=center_x, center_y=center_y)
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update_particle(self, dt: float) -> None:
        """Advance particle and fade alpha based on remaining lifetime."""
        self.center_x += self.velocity_x * dt
        self.center_y += self.velocity_y * dt
        self.lifetime -= dt
        if self.lifetime <= 0.0:
            self.kill()
            return

        alpha_ratio = max(0.0, min(1.0, self.lifetime / self.max_lifetime))
        self.alpha = int(255 * alpha_ratio)


class ParticleSystem:
    """Manage short-lived explosion particles."""

    def __init__(
        self,
        particles: arcade.SpriteList[arcade.Sprite] | None = None,
        rng: random.Random | None = None,
    ) -> None:
        """Initialize particle system storage and randomness source."""
        self._particles = particles if particles is not None else arcade.SpriteList()
        self._rng = rng if rng is not None else random.Random()
        self._texture_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "sprites"
            / "explosion_particle.png"
        )

    @property
    def particles(self) -> arcade.SpriteList[arcade.Sprite]:
        """Expose active particle list."""
        return self._particles

    def spawn_explosion(
        self, position: tuple[float, float], size: AsteroidSize
    ) -> None:
        """Spawn a short radial burst of particles for an asteroid explosion."""
        min_count, max_count, min_speed, max_speed = _explosion_profile(size)
        particle_count = self._rng.randint(min_count, max_count)
        for _ in range(particle_count):
            angle = self._rng.uniform(0.0, math.tau)
            speed = self._rng.uniform(min_speed, max_speed)
            lifetime = self._rng.uniform(0.3, 0.5)
            particle = _ExplosionParticle(
                texture_path=self._texture_path,
                center_x=position[0],
                center_y=position[1],
                velocity_x=math.cos(angle) * speed,
                velocity_y=math.sin(angle) * speed,
                lifetime=lifetime,
            )
            self._particles.append(particle)

    def update(self, dt: float) -> None:
        """Advance particle simulation and remove expired sprites."""
        for particle in list(self._particles):
            if isinstance(particle, _ExplosionParticle):
                particle.update_particle(dt)
            else:
                particle.update()
            if particle not in self._particles:
                continue
            if getattr(particle, "lifetime", 1.0) <= 0.0:
                particle.kill()

    def draw(self) -> None:
        """Draw all active particles."""
        self._particles.draw()


def _explosion_profile(size: AsteroidSize) -> tuple[int, int, float, float]:
    """Map asteroid size to particle count and velocity ranges."""
    if size is AsteroidSize.LARGE:
        return 10, 15, 120.0, 220.0
    if size is AsteroidSize.MEDIUM:
        return 8, 12, 90.0, 170.0
    return 5, 8, 60.0, 120.0
