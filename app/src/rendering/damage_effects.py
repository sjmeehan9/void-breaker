"""Damage feedback visual effects for player hits and destruction."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import arcade


@dataclass(slots=True)
class _DamageFlashEffect:
    sprite: arcade.Sprite
    original_color: tuple[int, int, int, int] | tuple[int, int, int]
    elapsed: float = 0.0
    duration: float = 0.2
    alternations: int = 4


@dataclass(slots=True)
class _InvulnerabilityEffect:
    sprite: arcade.Sprite
    elapsed: float = 0.0
    duration: float = 0.75


class _BurstParticle(arcade.SpriteSolidColor):
    """Simple sprite particle with velocity and fade-out lifetime."""

    def __init__(
        self,
        center_x: float,
        center_y: float,
        velocity_x: float,
        velocity_y: float,
        lifetime: float,
        color: tuple[int, int, int],
    ) -> None:
        super().__init__(6, 6, color)
        self.center_x = center_x
        self.center_y = center_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update_particle(self, dt: float) -> None:
        """Advance burst particle simulation and fade alpha."""
        self.center_x += self.velocity_x * dt
        self.center_y += self.velocity_y * dt
        self.lifetime -= dt
        if self.lifetime <= 0.0:
            self.kill()
            return
        self.alpha = int(
            max(0.0, min(255.0, 255.0 * self.lifetime / self.max_lifetime))
        )


class DamageEffects:
    """Manage player damage flash/flicker and destruction burst particles."""

    def __init__(self, rng: random.Random | None = None) -> None:
        """Initialise effect state and randomness source."""
        self._rng = rng if rng is not None else random.Random()
        self._flash_effects: list[_DamageFlashEffect] = []
        self._invulnerability_effects: list[_InvulnerabilityEffect] = []

    def trigger_damage_flash(self, sprite: arcade.Sprite) -> None:
        """Start a short red-white flash on the provided sprite."""
        existing = next(
            (effect for effect in self._flash_effects if effect.sprite is sprite),
            None,
        )
        original_color = getattr(sprite, "color", (255, 255, 255, 255))
        if existing is not None:
            existing.elapsed = 0.0
            existing.original_color = original_color
            return
        self._flash_effects.append(
            _DamageFlashEffect(sprite=sprite, original_color=original_color)
        )

    def trigger_invulnerability(
        self, ship: arcade.Sprite, duration: float = 0.75
    ) -> None:
        """Start/refresh visual flicker while a ship is invulnerable."""
        existing = next(
            (
                effect
                for effect in self._invulnerability_effects
                if effect.sprite is ship
            ),
            None,
        )
        if existing is not None:
            existing.elapsed = 0.0
            existing.duration = duration
            return
        self._invulnerability_effects.append(
            _InvulnerabilityEffect(sprite=ship, duration=duration)
        )

    def trigger_explosion(
        self,
        position: tuple[float, float],
        size: str,
        particle_list: arcade.SpriteList[arcade.Sprite],
    ) -> None:
        """Spawn enemy destruction particles at the given position."""
        del size
        self._spawn_particles(
            position=position,
            particle_list=particle_list,
            count_range=(5, 10),
            speed_range=(100.0, 200.0),
            lifetime_range=(0.3, 0.5),
            color=(255, 170, 40),
        )

    def trigger_destruction_sequence(
        self,
        position: tuple[float, float],
        particle_list: arcade.SpriteList[arcade.Sprite],
    ) -> None:
        """Spawn a larger burst for player-destruction feedback."""
        self._spawn_particles(
            position=position,
            particle_list=particle_list,
            count_range=(15, 20),
            speed_range=(150.0, 300.0),
            lifetime_range=(0.5, 0.8),
            color=(255, 120, 40),
        )

    def update(self, dt: float) -> None:
        """Advance effect timers and restore sprite state when finished."""
        for effect in list(self._flash_effects):
            effect.elapsed += dt
            if effect.elapsed >= effect.duration:
                effect.sprite.color = effect.original_color
                self._flash_effects.remove(effect)
                continue
            phase_count = max(1, effect.alternations * 2)
            phase = int((effect.elapsed / effect.duration) * phase_count)
            effect.sprite.color = (255, 0, 0) if phase % 2 == 0 else (255, 255, 255)

        for effect in list(self._invulnerability_effects):
            effect.elapsed += dt
            flicker = int(167.5 + 87.5 * math.sin(effect.elapsed * math.tau * 8.0))
            effect.sprite.alpha = max(80, min(255, flicker))
            if effect.elapsed >= effect.duration:
                effect.sprite.alpha = 255
                self._invulnerability_effects.remove(effect)

    def _spawn_particles(
        self,
        position: tuple[float, float],
        particle_list: arcade.SpriteList[arcade.Sprite],
        count_range: tuple[int, int],
        speed_range: tuple[float, float],
        lifetime_range: tuple[float, float],
        color: tuple[int, int, int],
    ) -> None:
        particle_count = self._rng.randint(*count_range)
        for _ in range(particle_count):
            angle = self._rng.uniform(0.0, math.tau)
            speed = self._rng.uniform(*speed_range)
            particle_list.append(
                _BurstParticle(
                    center_x=position[0],
                    center_y=position[1],
                    velocity_x=math.cos(angle) * speed,
                    velocity_y=math.sin(angle) * speed,
                    lifetime=self._rng.uniform(*lifetime_range),
                    color=color,
                )
            )
